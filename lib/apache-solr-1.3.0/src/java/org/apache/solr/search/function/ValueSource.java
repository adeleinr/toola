/**
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.apache.solr.search.function;

import org.apache.lucene.index.IndexReader;
import org.apache.solr.search.function.DocValues;

import java.io.IOException;
import java.io.Serializable;

/**
 * Instantiates {@link org.apache.solr.search.function.DocValues} for a particular reader.
 * <br>
 * Often used when creating a {@link FunctionQuery}.
 *
 * @version $Id: ValueSource.java 576683 2007-09-18 04:04:38Z yonik $
 */
public abstract class ValueSource implements Serializable {

  public abstract DocValues getValues(IndexReader reader) throws IOException;

  public abstract boolean equals(Object o);

  public abstract int hashCode();

  /** description of field, used in explain() */
  public abstract String description();

  public String toString() {
    return description();
  }

}
